/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package catalog.network;

import org.apache.commons.cli.Options;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.GnuParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.ParseException;
import org.openide.util.Exceptions;

import org.gephi.graph.api.*;
import org.gephi.data.attributes.api.AttributeColumn;
import org.gephi.data.attributes.api.AttributeController;
import org.gephi.data.attributes.api.AttributeModel;
import com.itextpdf.text.PageSize;
import java.awt.Rectangle;
import java.awt.geom.Rectangle2D;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.StringWriter;
import java.lang.reflect.Field;
import org.gephi.io.exporter.api.ExportController;
import org.gephi.io.exporter.preview.PDFExporter;
import org.gephi.io.exporter.spi.CharacterExporter;
import org.gephi.io.exporter.spi.Exporter;
import org.gephi.io.exporter.spi.GraphExporter;
import java.util.concurrent.TimeUnit;

import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.EdgeDefault;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.openide.util.Lookup;
import org.gephi.graph.api.DirectedGraph;
import org.gephi.graph.api.GraphController;
import org.gephi.graph.api.GraphModel;
import org.gephi.layout.plugin.AutoLayout;
import org.gephi.layout.plugin.force.StepDisplacement;
import org.gephi.layout.plugin.force.yifanHu.YifanHuLayout;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2;
import org.gephi.layout.plugin.labelAdjust.LabelAdjust;
import org.gephi.layout.plugin.scale.ScaleLayout;
import org.gephi.layout.plugin.scale.Expand;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.openide.util.Lookup;
import org.gephi.ranking.api.Ranking;
import org.gephi.ranking.api.RankingController;
import org.gephi.ranking.api.Transformer;
import org.gephi.ranking.plugin.transformer.AbstractColorTransformer;
import org.gephi.ranking.plugin.transformer.AbstractSizeTransformer;
import org.gephi.statistics.plugin.GraphDistance;
import org.gephi.data.attributes.api.AttributeColumn;
import org.gephi.data.attributes.api.AttributeController;
import org.gephi.data.attributes.api.AttributeModel;
import org.gephi.ranking.api.Ranking;
import org.gephi.ranking.api.RankingController;
import org.gephi.partition.api.Partition;
import org.gephi.partition.api.PartitionController;
import org.gephi.partition.plugin.NodeColorTransformer;

import org.gephi.visualization.impl.TextDataImpl;

import org.gephi.preview.api.PreviewModel;
import org.gephi.preview.api.PreviewController;
import org.gephi.preview.api.PreviewProperty;
import org.gephi.partition.api.Partition;
import org.gephi.partition.api.PartitionController;
import org.gephi.partition.plugin.NodeColorTransformer;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.gephi.statistics.plugin.Modularity;
import org.gephi.visualization.impl.TextDataImpl.TextLine;


/**
 *
 * @author matt
 */
public class CatalogNetwork {
    
    
    public static String graphFile;

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws NoSuchFieldException, IllegalArgumentException, IllegalAccessException {
        // TODO code application logic here
        
        //args = new String[]{ "-f /Users/matt/Dropbox/git/catalog-viz/test_11mill.gexf" };
        //args = new String[]{ "-f /Users/matt/Dropbox/git/catalog-viz/test first only.gexf" };
        //args = new String[]{ "-f /Users/matt/Dropbox/git/catalog-viz/io_gexf.gexf" };
                
        Options options = new Options();
        
        options.addOption("f", true, "file name");
        options.addOption("t", false, "number of ");        
        
        CommandLineParser parser = new GnuParser();
        
        try {
            CommandLine line = parser.parse( options, args);
            
            if( line.hasOption( "f" ) ) {
                
                System.out.println( line.getOptionValue( "f" ) );
                graphFile = line.getOptionValue( "f" ).trim();
                
                
                
            }else{
                System.out.println( "Need to specify the file with -f blah.gexf");
                System.exit(0);
            }
            
            
        } catch (ParseException ex) {
            Exceptions.printStackTrace(ex);
        }
        
        buildLayout();
        
        
    }
    
    public static void buildLayout() throws NoSuchFieldException, IllegalArgumentException, IllegalAccessException {
        
        String assetDir = graphFile.substring(0, graphFile.lastIndexOf('/')+1); 
        
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        
        pc.newProject();
        Workspace workspace = pc.getCurrentWorkspace();
        
        ImportController importController = Lookup.getDefault().lookup(ImportController.class);
        RankingController rankingController = Lookup.getDefault().lookup(RankingController.class);
        AttributeModel attributeModel = Lookup.getDefault().lookup(AttributeController.class).getModel();
        
        Container container;
        try {
            File file = new File(graphFile);            
            container = importController.importFile(file);
            
            
            
               
            container.getLoader().setEdgeDefault(EdgeDefault.UNDIRECTED);   //Force DIRECTED
            container.setAllowAutoNode(false);  //Don't create missing nodes
        } catch (Exception ex) {
            
            ex.printStackTrace();
            return;
        }
        
        
 
        //Append container to graph structure
        importController.process(container, new DefaultProcessor(), workspace);
        
        
        //See if graph is well imported
        GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getModel();
        DirectedGraph graph = graphModel.getDirectedGraph();
        System.out.println("Nodes: " + graph.getNodeCount());
        System.out.println("Edges: " + graph.getEdgeCount());

        
        //Rank color by Degree
        Ranking degreeRanking = rankingController.getModel().getRanking(Ranking.NODE_ELEMENT, Ranking.DEGREE_RANKING);
        AbstractSizeTransformer sizeTransformer = (AbstractSizeTransformer) rankingController.getModel().getTransformer(Ranking.NODE_ELEMENT, Transformer.RENDERABLE_SIZE);
        sizeTransformer.setMinSize(10);
        sizeTransformer.setMaxSize(1000);
        rankingController.transform(degreeRanking,sizeTransformer);
        
        
                
        //AbstractColorTransformer colorTransformer = (AbstractColorTransformer) rankingController.getModel().getTransformer(Ranking.NODE_ELEMENT, Transformer.RENDERABLE_COLOR);
        //colorTransformer.setColors(new Color[]{new Color(0xFEF0D9), new Color(0xB30000)});
        //rankingController.transform(degreeRanking,colorTransformer);

        //Rank size by centrality
        //AttributeColumn centralityColumn = attributeModel.getNodeTable().getColumn(GraphDistance.BETWEENNESS);
        //Ranking centralityRanking = rankingController.getModel().getRanking(Ranking.NODE_ELEMENT, centralityColumn.getId());
        //

        /*
          //Layout for 1 minute
        //Layout for 1 minute
        AutoLayout autoLayout = new AutoLayout(1, TimeUnit.MINUTES);
        autoLayout.setGraphModel(graphModel);
        YifanHuLayout firstLayout = new YifanHuLayout(null, new StepDisplacement(1f));
        ForceAtlas2 secondLayout = new ForceAtlas2(null);
        //AutoLayout.DynamicProperty adjustBySizeProperty = AutoLayout.createDynamicProperty("forceAtlas.adjustSizes.name", Boolean.TRUE, 0.1f);//True after 10% of layout time
        AutoLayout.DynamicProperty linLogMode = AutoLayout.createDynamicProperty("forceAtlas2.linLogMode.name", Boolean.TRUE, 0f);//500 for the complete period
        autoLayout.addLayout(firstLayout, 0.5f);
        autoLayout.addLayout(secondLayout, 0.5f, new AutoLayout.DynamicProperty[]{linLogMode});
        autoLayout.execute();

*/
        PartitionController partitionController = Lookup.getDefault().lookup(PartitionController.class);   
        
        //Run modularity algorithm - community detection
        
        Modularity modularity = new Modularity();
        
        //modularity.setResolution(new Double(1000000));
        modularity.execute(graphModel, attributeModel);
        
        System.out.println(modularity.getReport());
        
        AttributeColumn modColumn = attributeModel.getNodeTable().getColumn(Modularity.MODULARITY_CLASS);
        Partition p2 = partitionController.buildPartition(modColumn, graph);
        System.out.println(p2.getPartsCount() + " partitions found");
           
        
        NodeColorTransformer nodeColorTransformer2 = new NodeColorTransformer();
        nodeColorTransformer2.randomizeColors(p2);
        partitionController.transform(p2, nodeColorTransformer2);
        
        PreviewController previewController = Lookup.getDefault().lookup(PreviewController.class);
        PreviewModel model = previewController.getModel();
        model.getProperties().putValue(PreviewProperty.SHOW_NODE_LABELS, Boolean.TRUE);
        //model.getProperties().putValue(PreviewProperty.SHOW_NODE_LABELS, Boolean.FALSE);
        //model.getProperties().putValue(PreviewProperty.NODE_LABEL_PROPORTIONAL_SIZE, Boolean.TRUE);
        
        model.getProperties().putValue(PreviewProperty.EDGE_THICKNESS, 1);
        model.getProperties().putValue(PreviewProperty.ARROW_SIZE, 0);
        model.getProperties().putValue(PreviewProperty.SHOW_EDGES, Boolean.FALSE);
        //model.getProperties().putValue(PreviewProperty.NODE_LABEL_FONT, model.getProperties().getFontValue(PreviewProperty.NODE_LABEL_FONT).deriveFont(8));

        
        ForceAtlas2 layout = new ForceAtlas2(null);
        layout.setGraphModel(graphModel);
        layout.initAlgo();
        layout.resetPropertiesValues();

        //classic
        layout.setLinLogMode(Boolean.TRUE);
        layout.setEdgeWeightInfluence(new Double(1.0));
        layout.setScalingRatio(new Double(4));
        layout.setStrongGravityMode(Boolean.TRUE);
        layout.setGravity(new Double(0.02));
        layout.setThreadsCount(4);
        layout.setBarnesHutOptimize(Boolean.TRUE);
        layout.setBarnesHutTheta(new Double(1.2));
        
        /* modfied classic
        
        layout.setLinLogMode(Boolean.TRUE);
        layout.setEdgeWeightInfluence(new Double(2.0));
        layout.setScalingRatio(new Double(6));
        layout.setStrongGravityMode(Boolean.TRUE);
        layout.setGravity(new Double(0.03));
        layout.setThreadsCount(4);
        layout.setBarnesHutOptimize(Boolean.TRUE);
        layout.setBarnesHutTheta(new Double(1.2));
        */
        
        //layout.setLinLogMode(Boolean.TRUE);        
        //layout.setAdjustSizes(Boolean.TRUE);
        //layout.setEdgeWeightInfluence(new Double(0.75));
        //layout.setGravity(new Double(10000));
        //layout.setThreadsCount(8);
        //layout.setScalingRatio(new Double(5000));
        //layout.setOutboundAttractionDistribution(Boolean.TRUE);
        

        
        ExportController ec = Lookup.getDefault().lookup(ExportController.class);

        for (int i = 0; i < 50000 && layout.canAlgo(); i++) {
           layout.goAlgo();
           System.out.println( i);         
           
           if (i % 20 == 0){
               
                //Export
                try {
                    ec.exportFile(new File(assetDir + "autolayout.pdf"));
                } catch (IOException ex) {
                    ex.printStackTrace();
                }                   
                //Export
                try {
                    ec.exportFile(new File(assetDir + "tick_" + Integer.toString(i) + ".png"));
                } catch (IOException ex) {
                    ex.printStackTrace();
                }   
                

        
           }
           if (i % 500 == 0){
               
                GraphExporter exporter = (GraphExporter) ec.getExporter("gexf");     //Get GEXF exporter
                exporter.setWorkspace(workspace);
                try {
                    //ec.exportFile(new File(assetDir + "io_gexf_"+ Integer.toString(i) + ".gexf"), exporter);
                    ec.exportFile(new File(assetDir + "io_gexf_latest.gexf"), exporter);
                } catch (IOException ex) {
                    ex.printStackTrace();
                    return;
                }
        
           }
           
        }
        layout.endAlgo();
        
        Node[] nodes = graph.getNodes().toArray();
        for (int i = 0; i < nodes.length; i++)
        {
           //Get the TextDataImpl object
           TextDataImpl td=(TextDataImpl) nodes[i].getNodeData().getTextData();
           String labelText=nodes[i].getNodeData().getLabel();
           td.setText(labelText);
           //Could perhaps used getFontMetrics here to be more accurate but
           // this heuristic seems to work for me:
           Rectangle2D bounds=new Rectangle(labelText.length()*10,10);
           //Use reflection to set the protected Bounds data to non-zero sizes.
           Field protectedLineField = TextDataImpl.class.getDeclaredField("line");
           protectedLineField.setAccessible(true);        
           TextLine line = (TextLine) protectedLineField.get(td);
           line.setBounds(bounds);
        } 
        
        LabelAdjust layout2 = new LabelAdjust(null);
        layout2.resetPropertiesValues();
        layout2.setGraphModel(graphModel);
        layout2.initAlgo();
        
           for (int i = 0; i < 500 && layout2.canAlgo(); i++) {
           layout2.goAlgo();
           System.out.println( i);         
           
           if (i % 50 == 0){
               
                //Export
                try {
                    ec.exportFile(new File(assetDir + "autolayout.pdf"));
                } catch (IOException ex) {
                    ex.printStackTrace();
                }                   
                //Export
                try {
                    ec.exportFile(new File(assetDir + "tick_adjust_" + Integer.toString(i) + ".png"));
                } catch (IOException ex) {
                    ex.printStackTrace();
                }   
                

        
           }
           if (i % 500 == 0){
               
                GraphExporter exporter = (GraphExporter) ec.getExporter("gexf");     //Get GEXF exporter
                exporter.setWorkspace(workspace);
                try {
                    ec.exportFile(new File(assetDir + "io_gexf_adjust.gexf"), exporter);
                } catch (IOException ex) {
                    ex.printStackTrace();
                    return;
                }
        
           }
           
        }
        layout2.endAlgo();
        
        /*
        ScaleLayout layout3 = new ScaleLayout(new Expand(),new Double(0.8));
        layout3.resetPropertiesValues();
        
        layout3.setGraphModel(graphModel);
        
        layout3.initAlgo();
        
           for (int i = 0; i < 500; i++) {
           layout3.goAlgo();
           System.out.println( i);         
           
           if (i % 50 == 0){
               
                //Export
                try {
                    ec.exportFile(new File("/Users/matt/Dropbox/git/catalog-viz/autolayout.pdf"));
                } catch (IOException ex) {
                    ex.printStackTrace();
                }                   
                //Export
                try {
                    ec.exportFile(new File("/Users/matt/Dropbox/git/catalog-viz/tick_scale_" + Integer.toString(i) + ".png"));
                } catch (IOException ex) {
                    ex.printStackTrace();
                }   
                

        
           }
           if (i % 500 == 0){
               
                GraphExporter exporter = (GraphExporter) ec.getExporter("gexf");     //Get GEXF exporter
                exporter.setWorkspace(workspace);
                try {
                    ec.exportFile(new File("/Users/matt/Dropbox/git/catalog-viz/io_gexf_scale.gexf"), exporter);
                } catch (IOException ex) {
                    ex.printStackTrace();
                    return;
                }
        
           }
           
        }
        layout3.endAlgo();       
        
         */
        
   
    }
   
        
}
